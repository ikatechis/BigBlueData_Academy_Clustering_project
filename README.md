# Comics & ML
### BigBlueData_Academy_Clustering_project

This is the 4th project for the 2021-2022 Big Blue Academy Data Science Bootcamp. In this project, we use clustering to draw insights on what makes a comic book valuable!

### What makes a comic book valuable?

Comics books from the [Golden](https://en.wikipedia.org/wiki/Golden_Age_of_Comic_Books), like the first appearance of Superman, and [Silver age](https://en.wikipedia.org/wiki/Silver_Age_of_Comic_Books) of comics are [getting sold for millions in auctions](https://wealthygorilla.com/most-expensive-comic-books/). 

Modern-age comic books can also get really valuable within a couple of years (e.g. the first issue of The Walking Dead, also a hit TV series, is valued around 1800$). 

Unfortunately no one can predict whether a comic is going to rise in value beforehand! Could ML methods help with that?

### The Data

This dataset was scraped from [**comicbookrealm.com**](https://comicbookrealm.com/), a free price-guide website for american comic-books,  at the beginning of January 2022. 
It includes almost all data relevant to a comic issue like issue number, date, cover price, current value, synopsis, creators, characters, publisher, volume type,cover image link, cover variant, print number etc.

I plan to repeat the scraping from time to time in order to update the dataset with latest issues.

### Content

The dataset can be downloaded in .csv and .parquet format for a more convenient size:
**
Note: it all columns giving a link the address of the website `https://comicbookrealm.com/` should be added at the beginning of each string.**

Take a look at a [typical series link](https://comicbookrealm.com/series/5871/0/image-comics-the-walking-dead) to understand better all the relevant info

**`comic_data.csv`**:
Includes all information about each single issue that could be scraped. In detail:

`title`: the series title

`title_link`: the link to the title in the website

`issue_link`: the link to each issue of the title

`cover_link`: the link to the cover image of the issue

`issue`: the number of the issue

`cover_date`: the date (month and year) the issue was released

`cover_price`: the price in which the issue was sold

`current_value`: the highest price the issues was ever sold

`hist_price_link`: the link for the historical prices as recorder on the website

`searched`: the times the issue was searched in the site's database

`owned`: the times a user logged the issue as owned

`pages`: number of pages in issue

`rating`: the average rating by the site's users

`rating count`: the number of rating votes

`ISBN-UPC`: the unique issue code

`est_print_run`: the estimated number of copies printed

`variant_of`: if the issue is a variant cover of 

`preview`: if the issue is a preview

`synopsis`: brief description of the plot and/or issue edition  e.g. if it is a limited edition or exclusive etc.

`contributors_names`: lists of the names of the contributors

`contributors_roles`: lists that correspond to the role of each contributor (e.g. script, inks etc.)


`characters`: List of characters appearing in the issue as well as extra info (e.g. secret identity, link to character photo, special event like first appearance, death etc.) check on the the website for an example on the link above

`pub_id`: the unique publisher's id as given by the website

`volume`: volume number of the title or whether it is a one-shot, mini-series, limited-series etc.

`years`: The year span the title was published

`issues_total`: Total number of issues in the series

`pub_name`: The name of the publisher

`pub_titles_total`: total number of titles released by the publisher

`pub_issues_total `: total number of issues released by the publisher

### Inspiration
What makes a comic valuable?
What common characteristics do valuable comics share?
What other data would be needed to put odds on a comic book rising in value?
