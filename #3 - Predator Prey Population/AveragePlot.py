import pandas as pd
import matplotlib.pyplot as plt

# Initialize an empty list to store dataframes
dfs = []

# Loop through the 10 files and read them
for i in range(1, 11):
    # Construct the file name -> Energy free edition
    file_name = f"Assignments/Assignment_2/EneaEnergyFreeNoFlocking/DataTest_{i}.csv"

    # Construct the file name -> Energy edition
    #file_name = f"Assignments/Assignment_2/EnergyTestData1.1/DataTest_{i}.csv"

    # Read the file into a dataframe
    df = pd.read_csv(file_name)
    # Group by frame and type, then count occurrences
    grouped_df = df.groupby(['frame', 'Type']).size().reset_index(name='count')
    # Pivot the table to get counts for Fox and Rabbit in separate columns
    pivot_df = grouped_df.pivot(index='frame', columns='Type', values='count').fillna(0)
    # Append the pivot table to the list
    dfs.append(pivot_df)

# Create a figure and axis for the plot
plt.figure(figsize=(12, 6))

# Plot each individual file with transparency and smoothing
for pivot_df in dfs:
    pivot_df['Fox'] = pivot_df['Fox'].rolling(window=20, min_periods=1).mean()
    pivot_df['Rabbit'] = pivot_df['Rabbit'].rolling(window=20, min_periods=1).mean()

    plt.plot(pivot_df.index, pivot_df['Fox'], color='red', alpha=0.1, label='_nolegend_')
    plt.plot(pivot_df.index, pivot_df['Rabbit'], color='blue', alpha=0.1, label='_nolegend_')

# Concatenate all dataframes along the index (frame) and compute the mean
combined_df = pd.concat(dfs).groupby(level=0).mean()

# Apply rolling mean to the combined dataframe
combined_df['Fox'] = combined_df['Fox'].rolling(window=20, min_periods=1).mean()
combined_df['Rabbit'] = combined_df['Rabbit'].rolling(window=20, min_periods=1).mean()

# Plot the averaged data with solid lines
plt.plot(combined_df.index, combined_df['Fox'], label='Fox (Average)', color='red')
plt.plot(combined_df.index, combined_df['Rabbit'], label='Rabbit (Average)', color='blue')

# Add titles and labels
plt.title('Number of Foxes and Rabbits per Frame')
plt.xlabel('Frame Number')
plt.ylabel('Count')
plt.legend(title='Type')
plt.grid(True)

# Change this based on the graph height (brings out detail that would be missing when too zoomed out)
plt.ylim(0, 150)

# Energy Free Edition
plt.savefig('Assignments/Assignment_2/Results/EneaEnergyFreeNoFlocking_plot.png')

# Energy Edition
#plt.savefig('Assignments/Assignment_2/EnergyTestData1.1/foxes_rabbits_Energy_plot1.1.png')

# plt.show()


