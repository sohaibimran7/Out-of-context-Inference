Code for Out-of-context inference experiments

The experiments require a series of steps to run:

0. API key \
Make a .env file with your OpenAI API key as `OPENAI_API_KEY`

1. Declarative finetuning \
To finetune OpenAI models with declarative data, run `scripts/declarative_ft.ipynb`

2. Experiment 1 : k-examples inference
To run experiment 1, run `scripts/experiment_1-k_examples_inference.ipynb`

3. Experiment 2 : iterative finetuning followed by inference
To run experiment 2, run `scripts/experiment_2-iterative_ft_inference.ipynb`

Miscellaneous:

Experiment 0 : OOCR - Replicating [Berglund *et. al.*, (2023)](https://arxiv.org/abs/2309.00667) \
To run experiment 0, run `scripts/experiment_0.ipynb`

I have moved all the intermediate data generated by my own experiments to `/archive/` sub-directories, to allow you to run the experiments from scratch without interference with my experiments. This includes the declatarive finetuning now located in `data/archive/`, generated by the data augmentation process in `scripts/experiment_1-k_examples_inference.ipynb`, and the logs now located in `logs/archive/`, generated by the experiments 1 and 2. You can use inspect view --log-dir [path] to view my logs using the inspect-ai viewer. If you'd like to plot my results without rerunning the experiments, you will have to change the LOG_DIR variable values from `logs/` to `logs/archive/`. 
