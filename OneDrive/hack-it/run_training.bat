@echo off
echo ========================================
echo IRIS HEALTH ML/DL MODEL TRAINING
echo ========================================
echo.

echo Step 1: Setting up directories...
python prepare_training_data.py
echo.

echo Step 2: Installing ML/DL dependencies...
pip install -r requirements_ml.txt
echo.

echo Step 3: Ready to train!
echo.
echo Please add your training images to:
echo   - training_data/healthy/
echo   - training_data/unhealthy/
echo.
echo Then run: python train_iris_health_model.py
echo.
pause
