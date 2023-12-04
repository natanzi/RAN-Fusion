from pyfiglet import Figlet

# Create a Figlet object with the desired font
f = Figlet(font='big')

# Create the logo text
text = "Welcome to RANFusion"

# Create the logo
logo = f.renderText(text)

# Print the logo
print(logo)
