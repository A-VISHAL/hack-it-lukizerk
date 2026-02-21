"""
Setup Reference Images Script
Helps you set up the reference "good iris" images for comparison
"""

import cv2
import numpy as np
from pathlib import Path
from utils.segmentation import segment_iris, create_sector_map

def setup_reference_images(source_image_path):
    """
    Process a healthy iris image and create all reference images.
    
    Args:
        source_image_path: Path to the healthy iris image
    """
    print("=" * 60)
    print("REFERENCE IMAGE SETUP")
    print("=" * 60)
    
    # Create reference directory if it doesn't exist
    Path("reference").mkdir(exist_ok=True)
    
    # Check if source image exists
    if not Path(source_image_path).exists():
        print(f"❌ Error: Source image not found at {source_image_path}")
        print("\nPlease provide a healthy iris image.")
        return
    
    print(f"\n📁 Processing: {source_image_path}")
    
    # 1. Copy original as reference
    print("\n[1/3] Copying original image...")
    img = cv2.imread(source_image_path)
    reference_path = "reference/good_iris_reference.jpg"
    cv2.imwrite(reference_path, img)
    print(f"✅ Saved: {reference_path}")
    
    # 2. Create segmented iris
    print("\n[2/3] Creating segmented iris...")
    try:
        segmented_roi, original_image, circle_info = segment_iris(source_image_path)
        segmented_path = "reference/good_iris_segmented.jpg"
        cv2.imwrite(segmented_path, segmented_roi)
        print(f"✅ Saved: {segmented_path}")
        
        if circle_info['detected']:
            print(f"   ℹ️  Iris detected at center={circle_info['center']}, radius={circle_info['radius']}")
        else:
            print(f"   ⚠️  Using fallback segmentation")
    except Exception as e:
        print(f"❌ Error segmenting iris: {str(e)}")
        return
    
    # 3. Create sector map
    print("\n[3/3] Creating sector map...")
    try:
        sector_map, sector_analysis = create_sector_map(segmented_roi)
        sector_path = "reference/good_iris_sector_map.jpg"
        cv2.imwrite(sector_path, sector_map)
        print(f"✅ Saved: {sector_path}")
        
        # Display sector analysis
        print("\n📊 Sector Analysis:")
        for sector_name, data in sector_analysis.items():
            variation = data.get('variation', 0)
            print(f"   {sector_name}: {variation:.1f}% variation")
    except Exception as e:
        print(f"❌ Error creating sector map: {str(e)}")
        return
    
    print("\n" + "=" * 60)
    print("✅ REFERENCE IMAGES SETUP COMPLETE!")
    print("=" * 60)
    print("\nCreated files:")
    print(f"  1. {reference_path} - Original reference image")
    print(f"  2. {segmented_path} - Segmented iris ROI")
    print(f"  3. {sector_path} - Sector map with 8 divisions")
    print("\nThese images will now appear on the LEFT side in comparisons.")
    print("User uploaded images will appear on the RIGHT side.")
    print("\n🚀 You can now run the app: python -m streamlit run app.py")


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 60)
    print("REFERENCE IMAGE SETUP TOOL")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Image path provided as argument
        source_path = sys.argv[1]
        setup_reference_images(source_path)
    else:
        # Interactive mode
        print("\nThis tool will help you set up reference images for comparison.")
        print("\nYou need a high-quality image of a HEALTHY iris.")
        print("This will be used as the baseline for all comparisons.")
        
        # Check if there are any images in uploads folder
        uploads_dir = Path("uploads")
        if uploads_dir.exists():
            images = list(uploads_dir.glob("*.jpg")) + list(uploads_dir.glob("*.png"))
            if images:
                print(f"\n📁 Found {len(images)} images in uploads/ folder:")
                for i, img_path in enumerate(images[:10], 1):
                    print(f"   {i}. {img_path.name}")
                
                if len(images) > 10:
                    print(f"   ... and {len(images) - 10} more")
        
        print("\n" + "-" * 60)
        source_path = input("\nEnter path to healthy iris image: ").strip()
        
        if source_path:
            setup_reference_images(source_path)
        else:
            print("\n❌ No image path provided. Exiting.")
            print("\nUsage: python setup_reference_images.py <path_to_healthy_iris_image>")
