cd ..
sh ~/bin/n python main.py \
    "/data/dywang/Database/Proliferation/evaluation/mitko-picel-heatmaps-norm-full" --patch \
    --directory "/data/dywang/Database/Proliferation/libs/stage03_deepFeatMaps/results/patches_07-14-16/" \
    --mode "mitosis" \
    --pickle 0 # maybe make this 1 if this performs well 