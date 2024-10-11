import pandas as pd
import matplotlib.pyplot as plt

# Define the file name for the single dataset
file_name = "Assignments/Assignment_2/EnergyFlocking1/DataTest_1.csv"

# Read the file into a dataframe
df = pd.read_csv(file_name)

# Group by frame and type, then count occurrences
grouped_df = df.groupby(['frame', 'Type']).size().reset_index(name='count')

# Pivot the table to get counts for Fox and Rabbit in separate columns
pivot_df = grouped_df.pivot(index='frame', columns='Type', values='count').fillna(0)

# Apply rolling mean to smooth the data
pivot_df['Fox'] = pivot_df['Fox'].rolling(window=20, min_periods=1).mean()
pivot_df['Rabbit'] = pivot_df['Rabbit'].rolling(window=20, min_periods=1).mean()

# Create a figure and axis for the plot
plt.figure(figsize=(12, 6))

# Plot the smoothed data
plt.plot(pivot_df.index, pivot_df['Fox'], label='Fox', color='red')
plt.plot(pivot_df.index, pivot_df['Rabbit'], label='Rabbit', color='blue')

# Add titles and labels
plt.title('Number of Foxes and Rabbits per Frame')
plt.xlabel('Frame Number')
plt.ylabel('Count')
plt.legend(title='Type')
plt.grid(True)

# Change this based on the graph height (brings out detail that would be missing when too zoomed out)
plt.ylim(0, 200)

# Energy Free Edition
plt.savefig('Assignments/Assignment_2/EnergyFreeFlocking1/foxes_rabbits_plot_single.png')

# Energy Edition (uncomment if needed)
# plt.savefig('Assignments/Assignment_2/EnergyTestData1.1/foxes_rabbits_Energy_plot_single.png')

plt.show()
