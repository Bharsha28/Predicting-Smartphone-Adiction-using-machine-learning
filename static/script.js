async function predict() {
    const form = new FormData(document.getElementById("predictionForm"));
  
    const response = await fetch("/predict", {
      method: "POST",
      body: form,
    });
  
    const data = await response.json();
    document.getElementById("result").innerHTML = <h3>Result: ${data.result}</h3>;
  }