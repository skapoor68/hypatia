
out_path="good_paths_1/outs/"
out_path_end=".txt"
us="_"
for j in {2699..2669};
do
    for i in {0..3};
    do
        python good_paths_1.py $i $j > $out_path$i$us$j$out_path_end &
    done

    sleep 4m
done