import React from 'react';
import './App.css';
import MicRecorder from 'mic-recorder-to-mp3';

const Mp3Recorder = new MicRecorder({ bitRate: 128 });


class App extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      isRecording: false,
      blobURL: '',
      isBlocked: false,
    };
  }

  start = () => {
    console.log('Started');
    console.log(this.state.blobURL);
    if (this.state.isBlocked) {
      console.log('Permission Denied');
    } else {
      Mp3Recorder
        .start()
        .then(() => {
          this.setState({ isRecording: true });
        }).catch((e) => console.error(e));
    }
  };

  stop = () => {
    Mp3Recorder
      .stop()
      .getMp3()
      .then(([buffer, blob]) => {
        console.log('blobURL');
        // date and time
        var today = new Date();
        var date = today.getFullYear()+'_'+(today.getMonth()+1)+'_'+today.getDate();
        var time = today.getHours() + "_" + today.getMinutes() + "_" + today.getSeconds();
        var dateTime = date+'_'+time;
        //const myFile = new File(buffer, 'C:\\Users\\Acer\\flask-app\api\\imgs\\' + dateTime + ".mp3");
        //console.log("dateTime: "+ dateTime);
        const blobURL = URL.createObjectURL(blob);
        //console.log("NOWblobURL: "+ blobURL);
        var li = document.createElement('li');
        var link = document.createElement('a');
        var au = document.createElement('audio');
        var recordingsList = document.createElement("div")
        

        au.controls = true;
	      au.src = blobURL;

        link.href = blobURL;
        link.download = dateTime+".mp3"; //download forces the browser to donwload the file using the  filename
        link.innerHTML = "Save to disk";


        li.appendChild(au);
	
        //add the filename to the li
        li.appendChild(document.createTextNode(dateTime+".mp3"))

        //add the save to disk link to li
        li.appendChild(link); 
  

        // upload in order to process the video from the audio
        var upload = document.createElement('a');
        upload.href="#";
        upload.innerHTML = "Upload";
        upload.addEventListener("click", function(event){
            // here call backend uploader  
            var xhr=new XMLHttpRequest();
              xhr.onload=function(e) {
                if(this.readyState === 4) {
                  console.log("Server returned: ",e.target.responseText)
                }
              };
              var fd=new FormData();
              fd.append("audio_data",blob, 'filename.mp3');
              xhr.open("POST","https://videogenerators.com:5000/uploader",true);
              xhr.send(fd);

        })
        li.appendChild(document.createTextNode (" "))//add a space in between
        li.appendChild(upload)//add the upload link to li
      
        //add the li element to the ol
        recordingsList.appendChild(li);
        document.body.appendChild(recordingsList); 
       

        
        this.setState({blobURL, isRecording: false});
      }).catch((e) => console.log(e));

      
  };

  componentDidMount() {
    navigator.getUserMedia({ audio: true },
      () => {
        console.log('Permission Granted');
        this.setState({ isBlocked: false });
      },
      () => {
        console.log('Permission Denied');
        this.setState({ isBlocked: true })
      },
    );
  }

  

  render(){
    return (
      <div className="App">
        <header className="App-header">
          <button onClick={this.start} disabled={this.state.isRecording}>Record</button>
          <button onClick={this.stop} disabled={!this.state.isRecording}>Stop</button>
          <audio src={this.state.blobURL} controls="controls" />
          
        </header>
        <body>
          <p><strong>Recordings:</strong></p>
  	      <ol id="recordingsList"></ol>
        </body>
      </div>
    );
  }
}

export default App;
