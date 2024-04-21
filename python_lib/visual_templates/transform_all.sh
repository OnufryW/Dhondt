for INDEX in {1..41}
do
  python3 bmp_to_template.py ../../visual/templates/$INDEX.bmp district_647_700/${INDEX}.template
done
