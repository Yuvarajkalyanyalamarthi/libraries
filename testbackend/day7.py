import matplotlib.pyplot as plt

# 1. Define the data for the slices
sizes = [25, 30, 15, 30]

# 2. Define the labels for each slice
labels = ['Frogs', 'Hogs', 'Dogs', 'Logs']

# 3. Create the pie chart
# 'autopct' adds the percentage labels to each slice
plt.pie(sizes, labels=labels, autopct='%1.1f%%')

# 4. Add a title
plt.title('My First Pie Chart')

# 5. Ensure the pie is drawn as a circle (equal aspect ratio)
plt.axis('equal')  

# 6. Display the chart
plt.show()