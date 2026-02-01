import json
import glob
import os
import questionary
import statistics

def analyze_acc(filename: str):
    with open(filename, "r") as f:
        data = json.load(f)
        if not data:
            raise FileNotFoundError
        for benchmark_name, benchmark_data in data.items():
            print(f"{benchmark_name}:")
            statuslist = []
            for result in benchmark_data["results"]:
                statuslist.append(result["status"])

            success = statuslist.count("success")
            total = len(statuslist)
            
            persentage = (success/total) * 100

            print(f"{persentage}%")

    
def count_reasoning_patterns(filename: str, patterns: list):
    with open(filename, "r") as f:
        data = json.load(f)
        if not data:
            raise FileNotFoundError
        
        for benchmark_name, benchmark_data in data.items():
            print(f"{benchmark_name}:")


            reasoning = []

            try:
                for result in benchmark_data["results"]:
                    reasoning.append(result["reasoning"])
            except:
                print(f"Reasoningdata could not be extracted. Please check '{filename}' for reasoning traces.")
                exit()

            for patter in patterns:

                traces = 0
                times = 0

                for reasoningtarce in reasoning:
                    traces += 1
                    times += reasoningtarce.lower().count(patter)
                
                print(f"{patter} found {times/traces} times per response")


def reasoning_lenth_stats(filename):
    with open(filename, "r") as f:
        data = json.load(f)
        if not data:
            raise FileNotFoundError
        
        for benchmark_name, benchmark_data in data.items():
            print(f"{benchmark_name}:")

            reasoning = []

            try:
                for result in benchmark_data["results"]:
                    reasoning.append(result["reasoning"])
            except:
                print(f"Reasoningdata could not be extracted. Please check '{filename}' for reasoning traces.")
                exit()

            lenth = []
            wordcount = []
            word_length = []

            # add statistics to lists
            for reasoningtrace in reasoning:
                lenth.append(len(reasoningtrace))   # length in characters of each trace
                wordcount.append(len(reasoningtrace.split()))   # lenth in words of each trace
                for word in reasoningtrace.split():
                    word_length.append(len(word)) # lenth of each word

            print(f"Average characters: {statistics.mean(lenth)}")
            print(f"Average word count: {statistics.mean(wordcount)}")
            print()
            print(f"Median characters: {statistics.median(lenth)}")
            print(f"Median word count: {statistics.median(wordcount)}")
            print()
            print(f"Minimum characters: {min(lenth)}")
            print(f"Minimum word count: {min(wordcount)}")
            print()
            print(f"Maximum characters: {max(lenth)}")
            print(f"Maximum word count: {max(wordcount)}")
            print()
            print(f"Average word length: {statistics.mean(word_length)}")
            print(f"Median word length {statistics.median(word_length)}")

            


            


def main():
    files = glob.glob("results/*.json")
    selection = questionary.rawselect(
        "Which file do you want to get stats about?",
        choices=files,
    ).ask()
    
    analyze_acc(selection)
    count_reasoning_patterns(selection, ["wait", "pause", "hold on", "actually", "no,"])
    reasoning_lenth_stats(selection)



main()