const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
    alert("Speech Recognition not supported. Please use Google Chrome.");
}

const recognition = new SpeechRecognition();

recognition.lang = "hi-IN";      // Hindi language
recognition.continuous = false;
recognition.interimResults = false;

function startHindiVoice() {

    console.log("Hindi voice started");

    recognition.start();

}

recognition.onresult = function(event) {

    const transcript = event.results[0][0].transcript;

    console.log("Hindi Voice:", transcript);

    document.getElementById("searchInput").value = transcript;

};

recognition.onerror = function(event) {

    console.log("Voice Error:", event.error);

};