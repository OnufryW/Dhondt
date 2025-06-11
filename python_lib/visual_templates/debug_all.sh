for INDEX in {1..100}
do
  python3 template_to_bmp.py senate_1071_990/${INDEX}.template senate_1071_990/${INDEX}.bmp senate_1071_990/base.bmp
done
