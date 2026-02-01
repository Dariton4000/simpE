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
            
            percentage = (success/total) * 100

            print(f"{percentage}%")

    
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
                return

            for pattern in patterns:

                traces = 0
                times = 0

                for reasoningtrace in reasoning:
                    traces += 1
                    times += reasoningtrace.lower().count(pattern)
                
                print(f"{pattern} found {times/traces} times per response")


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
                return

            length = []
            wordcount = []
            word_length = []

            # add statistics to lists
            for reasoningtrace in reasoning:
                length.append(len(reasoningtrace))   # length in characters of each trace
                wordcount.append(len(reasoningtrace.split()))   # length in words of each trace
                for word in reasoningtrace.split():
                    word_length.append(len(word)) # length of each word

            print(f"Average characters: {statistics.mean(length)}")
            print(f"Average word count: {statistics.mean(wordcount)}")
            print()
            print(f"Median characters: {statistics.median(length)}")
            print(f"Median word count: {statistics.median(wordcount)}")
            print()
            print(f"Minimum characters: {min(length)}")
            print(f"Minimum word count: {min(wordcount)}")
            print()
            print(f"Maximum characters: {max(length)}")
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