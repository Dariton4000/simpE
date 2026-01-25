from openai import OpenAI
import os
import datetime
import random
import string


logs_directory = "logs"
results_directory = "results"

# leave empty to select currently loaded model
llm = ""




def log_message(message: str) -> None:
    timestamp = starttime.strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = os.path.join(logs_directory, f"log_{timestamp}.txt")
    l = open(log_filename, "a", encoding="utf-8")
    l.write(f"[{timestamp}] {message}\n")
    l.close()

def write_results(results: str, model : str) -> None:
    timestamp = starttime.strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = os.path.join(results_directory, f"result_{model.replace('/', '')}_{timestamp}.txt")
    l = open(log_filename, "a", encoding="utf-8")
    l.write(results)
    l.close()

def main(tries):

    log_message(f"Starting new eval with {tries} tries")
    
    model = ""

    results = []

    client = OpenAI(base_url="http://127.0.0.1:1234/v1")

    for t in range(tries):
        log_message(f"Starting test {t}")

        result = []

        stringlenth = random.randint(4, 10)
        text = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(stringlenth))

        result.append(text)

        try:
            starttime = datetime.datetime.now()

            # streaming to support reasoning output
            stream = client.responses.create(
                model=llm,
                reasoning={"effort": "medium", "summary": "detailed"},
                input=f"Provide the following text in reverse order. Don't output anything else. Only output the reversed string: \"{text}\"",
                stream=True,
            )

        except Exception as e:
            print("\nAn error occurred while making the API request.")
            log_message(f"An error occurred: {e}")
            continue

        reasoning_text = ""
        response = ""
        thinking = False
        has_thinking = False

        for event in stream:
            if event.type == "response.reasoning_text.delta":
                reasoning_text += event.delta
                thinking = True
                has_thinking = True
                running_for = datetime.datetime.now() - starttime

                # display of seconds laggy, needs fixing sometime in the future
                print(f"\rThinking... {running_for.total_seconds():.3f}s", end="")

            if event.type == "response.reasoning_text.done":
                thinking = False
                has_thinking = True
                log_message(f"[Reasoning]: {reasoning_text}")

            elif event.type == "response.output_text.delta":
                response += event.delta
                thinking = False
                print(f"\rResponding...", end="")
                
            elif event.type == "response.output_text.done":
                thinking = False
                print(f"\rResponse complete.", end="")

            elif event.type == "response.completed":
                model = event.response.model

        delta = datetime.datetime.now() - starttime
        result.append(delta.total_seconds())


        if has_thinking:
            result.append(reasoning_text)
        else:
            result.append("null")

        result.append(response)

        result.append(model)

        if response.strip() != text[::-1]:
            print(f"\nFail: {t+1}")
            log_message(f"Test {t+1} failed. Expected: {text[::-1]}, Got: {response.strip()}")
            result.append("fail")
        else:
            print()
            print("Success:", t+1)
            log_message(f"Success: {t+1}")
            result.append("success")

        results.append(result)

    write_results(str(results), model)


if __name__ == "__main__":
    global starttime
    starttime = datetime.datetime.now()

    # create logs directory
    try:
        os.mkdir(logs_directory)
        print(f"Directory '{logs_directory}' created successfully.")
    except FileExistsError:
        pass
    except PermissionError:
        print(f"Permission denied: Unable to create '{logs_directory}'.")
    except Exception as e:
        print(f"An error occurred, trying to create the logs directory: {e}")

    # creates results directory
    try:
        os.mkdir(results_directory)
        print(f"Directory '{results_directory}' created successfully.")
    except FileExistsError:
        pass
    except PermissionError:
        print(f"Permission denied: Unable to create '{results_directory}'.")
    except Exception as e:
        print(f"An error occurred, trying to create the results directory: {e}")

    main(100)
