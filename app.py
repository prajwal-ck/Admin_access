import process_request

def main():
    try:
        # Call the main function from process_request
        result = process_request.main()
        print("Script executed successfully!")
        print("Output:")
        print(result)
    except Exception as e:
        print("An error occurred:")
        print(e)

if __name__ == "__main__":
    main()
