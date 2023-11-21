#Provides functions to plot the network, cells, and UEs for visualization purposes.
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

# Set the location for the center of your map (e.g., Worcester, MA)
latitude_center = 42.2626  # Example latitude for Worcester, MA
longitude_center = -71.8023  # Example longitude for Worcester, MA

def plot_network(gNodeBs, UEs, show_cells=True, background_image_path='images/worcester_map.jpg'):
    fig, ax = plt.subplots(figsize=(10, 6))
        # If a background image path is provided, load and set it as the background
    if background_image_path:
        # Load the image
        img = Image.open(background_image_path)
        # Set the extent of the image to match the plot coordinates
        ax.imshow(img, extent=[0, 1000, 0, 1000], aspect='auto')

    # Define the coverage radius scale based on your coordinate system
    coverage_radius_scale = 300  # Adjust this value to represent 3 km on your plot

    # Plot gNodeBs and their coverage areas
    for gNodeB in gNodeBs:
        # Assuming gNodeB.Location is a tuple (x, y)
        gNodeB_x, gNodeB_y = gNodeB.Location
        # Draw the coverage area
        coverage_circle = mpatches.Circle((gNodeB_x, gNodeB_y), coverage_radius_scale, color='lightblue', alpha=0.5, label='Coverage Area' if gNodeB is gNodeBs[0] else "")
        ax.add_patch(coverage_circle)
        # Draw the gNodeB as a rectangle (or marker)
        ax.scatter(gNodeB_x, gNodeB_y, color='red', marker='^', s=100, label='gNodeB' if gNodeB is gNodeBs[0] else "")

        # Optionally, show cells
        #if show_cells:
            #for cell in gNodeB.Cells:
                #cell_x, cell_y = cell.Location
        ax.text(gNodeB_x, gNodeB_y, gNodeB.ID, color='black', fontsize=12)

    # Plot UEs
    for ue in UEs:
        ue_x, ue_y = ue.Location
        color = 'blue' if ue.ConnectedCellID is not None else 'gray'
        ax.scatter(ue_x, ue_y, color=color, marker='o', s=20, label='Connected UE' if ue.isConnected else "Unconnected UE")

    # Set labels and title
    ax.set_xlabel('Worcester City, MA')
    ax.set_ylabel('')
    ax.set_title('5G Network Simulation with Coverage Areas')

    # Show the legend only once
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))  # Removing duplicates in legend
    ax.legend(by_label.values(), by_label.keys())

    # Show grid
    ax.grid(True)

    # Display the plot
    plt.show()





