import streamlit as st
import google.generativeai as genai
import mimetypes
import time
import tempfile
from PIL import Image

input_type = st.selectbox("Select Input Type:", ["Text", "Text File", "Audio" , "image" , "video"])

if input_type == "Text":
    model = genai.GenerativeModel("gemini-1.5-flash")

    def get_gemini_resp(ques):
        result = model.generate_content(ques)
        return result.text

    st.header("Gemini")
    input = st.text_input("input" , key="input")
    submit = st.button("ask question")

    if submit:
        response = get_gemini_resp(input)
        st.subheader("the response is")
        st.write(response)


elif input_type == "Text File":
    st.title("File Upload and AI Analysis")
    st.write("Upload a video or text file, and our AI will process it.")

    # File uploader
    uploaded_file = st.file_uploader("Upload your file", type=["txt"])

    if uploaded_file is not None:
        # Save the uploaded file to a temporary directory
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(uploaded_file.read())
            file_path = temp_file.name

        
        st.write("Uploading text file...")
        text_file_genai = genai.upload_file(path=file_path)
        st.success(f"Completed upload: {text_file_genai.uri}")

                # Generate content for text files
        st.write("Generating summary for the text...")
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        result = model.generate_content([text_file_genai, "Summarize the text in a very efficient way and also in points"])

                # Display the response
        st.write("### AI Response")
        st.markdown(result.text)

elif input_type == "Audio" :
    st.title("Audio Description with Google Generative AI")

    # Upload the audio file
    uploaded_file = st.file_uploader("Upload an audio file (e.g., .m4a)", type=["m4a"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/m4a")  # Display the audio player
        st.write("Processing the uploaded audio file...")

        try:
            # Determine the MIME type of the uploaded file
            mime_type, _ = mimetypes.guess_type(uploaded_file.name)

            if mime_type is None:
                st.error("Could not determine the MIME type of the uploaded file.")

            # Upload the file to Google Generative AI
            myfile = genai.upload_file(uploaded_file, mime_type=mime_type)

            # Initialize the Generative AI model
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Generate content for the audio file
            result = model.generate_content([myfile, "describe this audio clip"])

            # Display the result
            st.markdown(result.text)

        except Exception as e:
            st.error(f"An error occurred: {e}")

elif input_type == "image":
    model = genai.GenerativeModel("gemini-1.5-flash")

    def get_gemini_res(inpu, image , prompt):
        if inpu != "":
            reponse = model.generate_content([inpu , image , prompt])
        else:
            reponse = model.generate_content(image)
        return reponse.text

    st.header("Gemini")
    input = st.text_input("input" , key="input")
    uploaded_file = st.file_uploader("choose an image" , type=["jpg" , "jpeg" , "png"])

    image = ""
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="uploaded image" , use_column_width=True)

    submit = st.button("tell me about the image")

    input_prompt ="""
    you are a special ai assistant to analyse image and answer the question in an effective and understandable way
    if he user ask {input} irrelevent to image, then just say sorry i can't give answer
    """

    if submit:
        response = get_gemini_res(input , image , input_prompt)
        st.subheader("the response is")
        st.write(response)

elif input_type == "video":
    st.title("Video Upload and AI Analysis")
    st.write("Upload a video file, and our AI will summarize it and generate a quiz with an answer key.")

    # File uploader
    video_file = st.file_uploader("Upload your video file", type=["mp4", "avi", "mov"])

    if video_file is not None:
        # Save the uploaded file to a temporary directory
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(video_file.read())
            video_path = temp_file.name

        st.write("Uploading file...")
        video_file_genai = genai.upload_file(path=video_path)
        st.success(f"Completed upload: {video_file_genai.uri}")

        # Check processing status
        st.write("Processing the file. Please wait...")
        while video_file_genai.state.name == "PROCESSING":
            st.write("Processing...")
            time.sleep(10)
            video_file_genai = genai.get_file(video_file_genai.name)

        if video_file_genai.state.name == "FAILED":
            st.error("File processing failed. Please try again.")

        # Create the prompt
        prompt = "Summarize this video. Then create a quiz with answer key based on the information in the video."

        # Choose a Gemini model
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")

        # Make the LLM request
        st.write("Making LLM inference request...")
        response = model.generate_content([video_file_genai, prompt],
                                          request_options={"timeout": 600})

        # Display the response
        st.write("### AI Response")
        st.markdown(response.text)

else:
    st.write("some thing wrong")