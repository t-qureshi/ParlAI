import os

import argparse
import ast
from os import listdir
from os.path import isfile, join

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--logdir', type=str, default=None, help="Place all the run.sh perturb outputs in a logdir")
parser.add_argument('--target_filetype', type=str, default='csv')


args = parser.parse_args()

class Converter(object):
    def __init__(self, args):
        self.args = args
        self.logdir = args.logdir
        self.filenames = [join(self.logdir, f) for f in listdir(self.logdir) if isfile(join(self.logdir, f)) and ".txt" in f]
        self.valid_metrics = ['ppl', 'f1', 'bleu']
        self.parsed_data = {}
        assert self.filenames
        for filename in self.filenames:
            self.parsed_data[filename] = self.parse(filename)

    def parse(self, filename):
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines()]

        data = {}
        data["metric_values"] = []
        data["metric_types"] = []
        
        lid = 0
        while lid < len(lines):
            if "MODELTYPE" in lines[lid]:
                data['modeltype'] = lines[lid].split(":")[-1].strip()
            if "CONFIG :" in lines[lid]:
                perturb_type = lines[lid].split("test_")[-1]
                assert "FINAL_REPORT: " in lines[lid+1]
                metrics_str = lines[lid+1].split("FINAL_REPORT: ")[-1]
                metrics = ast.literal_eval(metrics_str)
                for metric_type in self.valid_metrics:
                    data["metric_values"].append("{0:.2f}".format(metrics[metric_type]))
                    data["metric_types"].append("{}_{}".format(perturb_type, metric_type))
            lid += 1
        return data

    def convert(self):
        if self.args.target_filetype == "csv":
            print("Conversting to a csv file...")
            self.convert_to_csv()
        else:
            assert "unsupported type : {}. Valid : csv".format(self.args["target_filetype"])

    def convert_to_csv(self):
        target_filename = join(self.logdir, "logs.csv")
        with open(target_filename, 'w') as f:
            for i, filename in enumerate(self.filenames):
                parsed_data = self.parsed_data[filename]
                if i == 0:
                    line1 = "Model, " + " , ".join(parsed_data["metric_types"])
                    f.write("{}\n".format(line1))
                line = "{}, ".format(parsed_data['modeltype']) + " , ".join(parsed_data["metric_values"])
                f.write("{}\n".format(line))
                print("Writing line {}".format(i+1))
        print("Done writing to {}".format(target_filename))
                    
if __name__ == "__main__":
    converter = Converter(args)
    converter.convert()
