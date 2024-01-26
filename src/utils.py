def from_assistant_message_to_posts(assistant_message, user_message=None):
    posts = []
    for content in assistant_message.content:
        if content.type == "text":
            posts.append(content.text.value)
    if user_message is not None and user_message == posts[-1]:
        posts[
            -1
        ] = "There was some problem on OpenAI server. Please, try your request again. Thank you!"
    return posts
