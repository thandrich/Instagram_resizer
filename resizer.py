def get_aspect_ratio(image):
    width, height = image.size
    return width / height

def rotate_image(image):
    return image.rotate(90, expand=True)

def process_image(filepath, output_folder, target_width):
    portrait_ratio_threshold = 4 / 5
    landscape_ratio_threshold = 8 / 5
    tolerance = -1e-6 # Defining tolerance to get around floating point precission issues
    try:
        # Open the image file
        with Image.open(filepath) as img:
            aspect_ratio = get_aspect_ratio(img)
            slices = 1

            if aspect_ratio == 1:  # Square aspect ratio
                new_width = new_height = target_width
            elif portrait_ratio_threshold <= aspect_ratio < 1:  # Portrait aspect ratio >= 4:5
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            elif 1 / landscape_ratio_threshold < aspect_ratio < portrait_ratio_threshold:  # Portrait with odd aspect ratio
                img = rotate_image(img)
                aspect_ratio = get_aspect_ratio(img)
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            elif 0 < aspect_ratio <= 1 / landscape_ratio_threshold:  # Portrait with long aspect ratio
                img = rotate_image(img)
                aspect_ratio = get_aspect_ratio(img)
                slices = int(aspect_ratio // (portrait_ratio_threshold + tolerance))  # Floor division of aspect ratio over max portrait aspect ratio
                new_width = target_width
                new_height = int(target_width / aspect_ratio) * slices
            elif 1 < aspect_ratio < landscape_ratio_threshold:  # Landscape aspect ratio < 8:5
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            elif aspect_ratio >= landscape_ratio_threshold:  # Landscape aspect ratio >= 8:5
                slices = int(aspect_ratio // (portrait_ratio_threshold + tolerance))  # Floor division of aspect ratio over max portrait aspect ratio
                new_width = target_width
                new_height = int(target_width / aspect_ratio) * slices

            # Calculate the width of each slice
            slice_width = img.width // slices

            # Extract the original filename (excluding extension)
            filename = os.path.splitext(os.path.basename(filepath))[0]

            # Generate and save each slice
            for i in range(slices):
                left = i * slice_width
                right = (i + 1) * slice_width
                sliced_img = img.crop((left, 0, right, img.height))
                resized_img = sliced_img.resize((new_width, new_height), Image.LANCZOS)

                # Convert to RGB mode if the image is in RGBA mode
                if resized_img.mode == 'RGBA':
                    resized_img = resized_img.convert('RGB')

                # Save the sliced image with the original filename and index
                output_filename = f"{filename}_processed_{i+1}.jpg"
                output_filepath = os.path.join(output_folder, output_filename)
                resized_img.save(output_filepath)

    except Exception as e:
        # Handle any exceptions (e.g., file not found, not a valid image)
        print(f"Error: {e}")
    
# Processing loop
def process_images_in_folder(folder_path):

    # Get user input for the output folder and target width
    output_folder = input("Enter the output folder name (press Enter for default - output): ")

    # Check if the user entered anything; if not, set a default value
    output_folder = output_folder.strip() or "output"

    target_width_input = input("Enter the target width in px (press Enter for default - 1080): ")

    # Check if the user entered anything; if not, set a default value
    target_width = int(target_width_input) if target_width_input.strip() else 1080

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # List all files in the current folder
    files = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]

    # Process each JPEG file
    for file in files:
        file_path = os.path.join(folder_path, file)
        process_image(file_path, output_folder, target_width)

# Script execution        
current_folder = os.getcwd()  # Get the current working directory
process_images_in_folder(current_folder)