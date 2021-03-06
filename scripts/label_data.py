import datasets
import pandas as pd


def load_and_save_data(path: str):
    data = datasets.load_dataset(path)
    for split in data.keys():
        data[split].set_format('pandas')
        data[split].to_csv(f'{path}_{split}.tsv', sep='\t', encoding='utf8')


load_and_save_data('blended_skill_talk')
