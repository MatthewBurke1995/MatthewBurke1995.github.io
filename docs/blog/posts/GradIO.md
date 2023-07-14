---
date: 2023-01-01
categories:
  - Python
  - Machine Learning
  - NLP
---



#Gradio

I've been taking Jeremy Howard's ["Practical Deep Learning for Coders"](https://course.fast.ai/Lessons/lesson2.html). The course is practical so it's no surprise that it discusses deployment during Lesson Two and in the process introduces the `gradio` package. 

<!-- more -->

Gradio makes a good use case for demonstrating deep learning models. The skill sets for starting up a webserver, creating a deep learning model and writing javascript for the presentation layer are different and having to do them all at once can be frustrating. Gradio takes care of the webserver and frontend part of the sandwich so you can focus on the meatier functionality bits.

It's a good use case but there is still the issue of deploying the gradio application to the internet on a machine that can handle deep learning workloads. Thankfully last year Hugging Face added ["Hugging Face Spaces"](https://huggingface.co/spaces/launch) to their suite of tools. Each space has a limit of 16GB RAM and 8 CPU cores and hosts a docker container exposed to the internet.

Last year I published a Korean language sentiment analysis pipeline to Hugging Faces, so I'll be using that as the basis for the gradio deployment.

You can find the language model [here](https://huggingface.co/matthewburke/korean_sentiment). And the repository for the gradio application [here](https://huggingface.co/spaces/matthewburke/KoreanSentiment). Since it's hosted on a site which allows CORS I can call to it from this frontend without any issues. One last thing about the model is that it's trained on movie review data, if you give it the phrase "눈물 났다" ("I shed a tear") it will predict it as having a positive sentiment with a >95% confidence rating.

<input placeholder="종았다" id="sentence" type="text">
<input class="md-button" type="submit" id="submitbutton">
<div id="results"></div>
<script>
  function updateValue(event) {
    text = document.getElementById('sentence').value;
    console.log(text);
    fetch("https://matthewburke-koreansentiment.hf.space/run/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        data: [
          text,
        ]
      })})
    .then(r => r.json())
    .then(
      r => {
        var str = JSON.stringify(r.data, null, 2); //
        results.innerHTML = str;
      }
    )

  }

  submitbutton.addEventListener('click', updateValue);
</script>

