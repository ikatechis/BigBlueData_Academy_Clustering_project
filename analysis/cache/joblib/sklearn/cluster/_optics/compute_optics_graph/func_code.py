# first line: 398
def compute_optics_graph(
    X, *, min_samples, max_eps, metric, p, metric_params, algorithm, leaf_size, n_jobs
):
    """Computes the OPTICS reachability graph.

    Read more in the :ref:`User Guide <optics>`.

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features), or \
            (n_samples, n_samples) if metric=’precomputed’.
        A feature array, or array of distances between samples if
        metric='precomputed'

    min_samples : int > 1 or float between 0 and 1
        The number of samples in a neighborhood for a point to be considered
        as a core point. Expressed as an absolute number or a fraction of the
        number of samples (rounded to be at least 2).

    max_eps : float, default=np.inf
        The maximum distance between two samples for one to be considered as
        in the neighborhood of the other. Default value of ``np.inf`` will
        identify clusters across all scales; reducing ``max_eps`` will result
        in shorter run times.

    metric : str or callable, default='minkowski'
        Metric to use for distance computation. Any metric from scikit-learn
        or scipy.spatial.distance can be used.

        If metric is a callable function, it is called on each
        pair of instances (rows) and the resulting value recorded. The callable
        should take two arrays as input and return one value indicating the
        distance between them. This works for Scipy's metrics, but is less
        efficient than passing the metric name as a string. If metric is
        "precomputed", X is assumed to be a distance matrix and must be square.

        Valid values for metric are:

        - from scikit-learn: ['cityblock', 'cosine', 'euclidean', 'l1', 'l2',
          'manhattan']

        - from scipy.spatial.distance: ['braycurtis', 'canberra', 'chebyshev',
          'correlation', 'dice', 'hamming', 'jaccard', 'kulsinski',
          'mahalanobis', 'minkowski', 'rogerstanimoto', 'russellrao',
          'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean',
          'yule']

        See the documentation for scipy.spatial.distance for details on these
        metrics.

    p : int, default=2
        Parameter for the Minkowski metric from
        :class:`~sklearn.metrics.pairwise_distances`. When p = 1, this is
        equivalent to using manhattan_distance (l1), and euclidean_distance
        (l2) for p = 2. For arbitrary p, minkowski_distance (l_p) is used.

    metric_params : dict, default=None
        Additional keyword arguments for the metric function.

    algorithm : {'auto', 'ball_tree', 'kd_tree', 'brute'}, default='auto'
        Algorithm used to compute the nearest neighbors:

        - 'ball_tree' will use :class:`BallTree`
        - 'kd_tree' will use :class:`KDTree`
        - 'brute' will use a brute-force search.
        - 'auto' will attempt to decide the most appropriate algorithm
          based on the values passed to :meth:`fit` method. (default)

        Note: fitting on sparse input will override the setting of
        this parameter, using brute force.

    leaf_size : int, default=30
        Leaf size passed to :class:`BallTree` or :class:`KDTree`. This can
        affect the speed of the construction and query, as well as the memory
        required to store the tree. The optimal value depends on the
        nature of the problem.

    n_jobs : int, default=None
        The number of parallel jobs to run for neighbors search.
        ``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.
        ``-1`` means using all processors. See :term:`Glossary <n_jobs>`
        for more details.

    Returns
    -------
    ordering_ : array of shape (n_samples,)
        The cluster ordered list of sample indices.

    core_distances_ : array of shape (n_samples,)
        Distance at which each sample becomes a core point, indexed by object
        order. Points which will never be core have a distance of inf. Use
        ``clust.core_distances_[clust.ordering_]`` to access in cluster order.

    reachability_ : array of shape (n_samples,)
        Reachability distances per sample, indexed by object order. Use
        ``clust.reachability_[clust.ordering_]`` to access in cluster order.

    predecessor_ : array of shape (n_samples,)
        Point that a sample was reached from, indexed by object order.
        Seed points have a predecessor of -1.

    References
    ----------
    .. [1] Ankerst, Mihael, Markus M. Breunig, Hans-Peter Kriegel,
       and Jörg Sander. "OPTICS: ordering points to identify the clustering
       structure." ACM SIGMOD Record 28, no. 2 (1999): 49-60.
    """
    n_samples = X.shape[0]
    _validate_size(min_samples, n_samples, "min_samples")
    if min_samples <= 1:
        min_samples = max(2, int(min_samples * n_samples))

    # Start all points as 'unprocessed' ##
    reachability_ = np.empty(n_samples)
    reachability_.fill(np.inf)
    predecessor_ = np.empty(n_samples, dtype=int)
    predecessor_.fill(-1)

    nbrs = NearestNeighbors(
        n_neighbors=min_samples,
        algorithm=algorithm,
        leaf_size=leaf_size,
        metric=metric,
        metric_params=metric_params,
        p=p,
        n_jobs=n_jobs,
    )

    nbrs.fit(X)
    # Here we first do a kNN query for each point, this differs from
    # the original OPTICS that only used epsilon range queries.
    # TODO: handle working_memory somehow?
    core_distances_ = _compute_core_distances_(
        X=X, neighbors=nbrs, min_samples=min_samples, working_memory=None
    )
    # OPTICS puts an upper limit on these, use inf for undefined.
    core_distances_[core_distances_ > max_eps] = np.inf
    np.around(
        core_distances_,
        decimals=np.finfo(core_distances_.dtype).precision,
        out=core_distances_,
    )

    # Main OPTICS loop. Not parallelizable. The order that entries are
    # written to the 'ordering_' list is important!
    # Note that this implementation is O(n^2) theoretically, but
    # supposedly with very low constant factors.
    processed = np.zeros(X.shape[0], dtype=bool)
    ordering = np.zeros(X.shape[0], dtype=int)
    for ordering_idx in range(X.shape[0]):
        # Choose next based on smallest reachability distance
        # (And prefer smaller ids on ties, possibly np.inf!)
        index = np.where(processed == 0)[0]
        point = index[np.argmin(reachability_[index])]

        processed[point] = True
        ordering[ordering_idx] = point
        if core_distances_[point] != np.inf:
            _set_reach_dist(
                core_distances_=core_distances_,
                reachability_=reachability_,
                predecessor_=predecessor_,
                point_index=point,
                processed=processed,
                X=X,
                nbrs=nbrs,
                metric=metric,
                metric_params=metric_params,
                p=p,
                max_eps=max_eps,
            )
    if np.all(np.isinf(reachability_)):
        warnings.warn(
            "All reachability values are inf. Set a larger"
            " max_eps or all data will be considered outliers.",
            UserWarning,
        )
    return ordering, core_distances_, reachability_, predecessor_
