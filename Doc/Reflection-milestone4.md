So far, all four main plots have been completed using daily data.

### The current content of the dashboard includes:
- Plot 1. Line plot: Comparison of global indices
- Plot 2. Bar chart: Growth rate for each sector
- Plot 3. Line plot: Close price of the top 5 companies in each sector
- Plot 4. Pie chart: Volume of the top 5 companies in each sector

### What we have implemented
Plot 1(line), Our dashboard provides users with the flexibility to compare not only the S&P500 with other global indices, but also different sectors within the S&P500 with either the S&P500 or other global indices. Users can select from a range of options in the dropdown menu, including "S&P original", "S&P energy", "S&P industry", "S&P consumer", "FTSE 100", "Euro Stoxx 50", "Hang Seng" and "Nikkei 225". This allows users to analyze the performance of different sectors and indices and identify trends or patterns that may not be immediately apparent.
The legend in our dashboard provides users with the option to toggle between displaying one line or two lines on the graph. Additionally, when the user hovers their mouse over a specific point on the line graph, a tooltip appears showing the corresponding data and numerical value for that point. This allows for more detailed and precise analysis of the data.

Plot 2(bar chart), calculates the growth rate based on a selected time period that ranges from the largest to the smallest. This enables users to compare and contrast the growth rates of different sectors over a specific time frame and identify which ones have experienced the highest or lowest rates of growth. Also, hovering over a bar will display the top 5 companies in that sector.

Plot 3(line) and Plot 4(pie chart) offer users the option to select a sector from a dropdown menu that includes 10 options: "Health care", "Information technology", "Utilities", "Energy", "Industries", "Consumer Discretionary", "Real estate","Consumer staples","Materials", and "Communication service". Once a sector is chosen, Plot 3 will display a line chart showcasing the top 5 companies in terms of growth rate for that sector, while Plot 4 will display a pie chart illustrating the volume proportion of those top 5 companies.

### What is not yet implemented
Minute data was not included at a later stage due to the substantial size of the dataset,and downloading and processing can be time-consuming and inconvenient for users when launching the app.Furthermore, users tend to be more interested in daily or monthly durations rather than minute-by-minute data.

### Reflection on suggestion from TA
About user experience, TA said all the graphs are properly working. The graphs are very easy to understand and the functions are easy to use and are interactive 

TA suggested we can try to add FTSE 100, Euro, Hang Seng and Nikkei 225 to Tab2 and Tab3.This is a great idea, as it would expand the dashboard's usefulness to include various global indices. As our current target users are North American investors and due to the time limitation, we prioritize the SP500 currently. We plan to add more global indices to Tabs 2 and 3 in the near future.
