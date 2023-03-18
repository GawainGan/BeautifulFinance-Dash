# Stock Market Dashboard

Link to our dashboard: TBD

![sketch](sketch.jpeg)


Welcome to our stock market dashboard! This dashboard provides a variety of visualizations to help users explore and understand stock market trends and performance.

## Motivation

We created this dashboard to make it easier for traders and investors to access and evaluate crucial stock market data fast. Our objective is to offer a simple and user-friendly interface that makes it simple for consumers to spot trends and take wise judgments.

## Updates

The latest updates to the dashboard include:

1. Adding a moving average function to Tab 1.
2. Incorporating a checklist option in Tab 1, allowing for the generation of multiple moving average trends simultaneously.
3. Modifying the growth rate calculation method in Tab 2.
4. Introducing hovertext in Tab 2. Each sector's bar will now display the top 5 companies, sorted by ascending growth rate, when hovered over.


## Usage

The primary components of our dashboard are a sidebar on the left and 3 tabs on the right. In addition to time selectors for deciding what time period should be shown on the graphs, the sidebar provides general information about other stock markets in the world.

1. Tab 1:
    - The trend plot shows the trend of the stock market prices over time.
    - Users can compare various stock markets using a dropdown menu option, 
    - Users can also choose moving average period via a checklist option, allowing for the generation of multiple moving average trends simultaneously.

2. Tab 2:
    - The growth and decline rates of each GICS sector of the SP500 are displayed in the bar chart in tab 2, with an updated calculation method.
    - The bar chart now includes hover text, displaying GICS sector name, the growth rate, and the top 5 companies when hovered over.

3. Tab 3:
    - The two plots allow users to examine the top 5 companies in a particular sector by selecting it from the dropdown list. 
    - Users can select which companies to display using the checklist selector, which displays the price change for the selected companies. 
    - The percentage of volume for the chosen companies is displayed in the pie chart on the right.


## Contributing

Anyone interested in helping us improve our dashboard is welcome to contribute. Clone our repository, then use pip to install the required dependencies. The python app.py command can then be used to run the application locally. To assist us in improving the dashboard, feel free to submit bug reports, feature requests, or pull requests.

We appreciate you utilizing our dashboard! We sincerely hope you find it insightful and helpful. Please get in touch with us if you have any inquiries or comments.
