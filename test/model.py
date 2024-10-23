import requests
import json

# Define the list of natural questions
questions = [
    "What time can I check in/check out?",
    "How do I access the property? Is there a key or code I need?",
    "Is parking available? If so, is it free, and where is it located? Does the property have EV charging, and how does it work? Are there any additional fees or instructions for using the charger?",
    "What is the Wi-Fi password, does it work in all areas of the house, and how reliable is the internet connection?",
    "What kind of TV does the property have? Can I cast to it from my device, and does it have streaming services like Netflix, Disney+, Hulu, or others available?",
    "Can you recommend good restaurants, attractions, or things to do nearby?",
    "Is it possible to check in early or check out late?",
    "What are the transportation options in the area? Is there easy access to Uber, Lyft, taxis, or local ride-sharing services? Are there public transportation options nearby?",
    "Are there any specific house rules I should be aware of, such as quiet hours?",
    "Is the kitchen fully equipped for cooking? What specific appliances or cookware are available? Are there any basics such as oil, salt/pepper, coffee filters?",
    "Is there a washing machine or dryer available for use? How do I access it? Is there detergent or do I need to buy some?",
    "Are extra towels or bedding available if needed?",
    "How do I control the heating or air conditioning in the property?",
    "Is the property pet-friendly, and are there any restrictions for pets?",
    "Where should I dispose of trash and recycling during my stay? Is there recycling? What can be recycled?",
    "Is the property child-friendly, and are there any baby essentials like cribs or high chairs available?",
    "Is the neighborhood safe, and are there any security measures at the property?",
    "Are there nearby grocery stores or markets where I can buy essentials?",
    "What is your cancellation policy if my plans change?",
    "Who should I contact in case of maintenance problems (e.g., plumbing, electricity)?",
]

# Define the endpoint URL
url = "https://amastay.develop.amastay.amastayai.com/api/v1/model/query"

# Iterate over the questions and make the requests
for question in questions:
    payload = {
        "message": question,
        "booking_id": "716d2a04-661d-49cc-8d3d-c13beb2d05cd",
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6IjN6RVo0Y2Nya2dWdEg0a2IiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2hnYnJncHB5cGF0bWljdGRhZXp5LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJmYzFjZjUyZi1lNjhiLTQ1ZmEtODE4NS1hNWE5MTUwNzhiZTYiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzI4NDI2NTI4LCJpYXQiOjE3Mjg0MjI5MjgsImVtYWlsIjoiIiwicGhvbmUiOiIxNDE1NjAyNTM4MSIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6InBob25lIiwicHJvdmlkZXJzIjpbInBob25lIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZXN0aW1hdGVkX3Byb3BlcnRpZXMiOjEwLCJmaXJzdF9uYW1lIjoiQnJpYW4iLCJsYXN0X25hbWUiOiJQZXJpbiIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwic3ViIjoiZmMxY2Y1MmYtZTY4Yi00NWZhLTgxODUtYTVhOTE1MDc4YmU2In0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoib3RwIiwidGltZXN0YW1wIjoxNzI4NDEzNjYxfV0sInNlc3Npb25faWQiOiIyZTZjMGFjMy1iMzA5LTQxNTEtYmVmZC01MDdkZGQ4ZGNhYzEiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.z33NFWyvayQs-Rwg-x7wZdUcNdp8ZRO9FZVnKMcr2-Y",
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Print the question and the response
    print(f"Question: {question}")
    print(f"Response: {response.json()}\n")
