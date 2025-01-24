import 'core-js/stable';
import 'regenerator-runtime/runtime';
import {
  LocalUser,
  RemoteUser,
  useIsConnected,
  useJoin,
  useLocalMicrophoneTrack,
  useLocalCameraTrack,
  usePublish,
  useRemoteUsers,
} from "agora-rtc-react";
import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";
import axios from 'axios';

import "./index.css";

const MeetingProgress = () => {
  const location = useLocation();
  const { appID, channelName, token } = location.state || {};

  const [calling, setCalling] = useState(false);
  const isConnected = useIsConnected();

  // 状態を追加
  const [appId, setAppId] = useState(appID);
  const [channel, setChannel] = useState(channelName);
  const [tokenValue, setToken] = useState(token);

  useJoin(
    { appid: appId, channel: channel, token: tokenValue ? tokenValue : null },
    calling
  );

  //local user
  const [micOn, setMic] = useState(true);
  const [cameraOn, setCamera] = useState(true);
  const { localMicrophoneTrack } = useLocalMicrophoneTrack(micOn);
  const { localCameraTrack } = useLocalCameraTrack(cameraOn);
  usePublish([localMicrophoneTrack, localCameraTrack]);
  //remote users
  const remoteUsers = useRemoteUsers();

  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  useEffect(() => {
    if (!browserSupportsSpeechRecognition) return;

    if (isConnected) {
      if (micOn && !listening) {
        SpeechRecognition.startListening();
      } else if (!micOn && listening) {
        SpeechRecognition.stopListening();
      }
    } else if (listening) {
      SpeechRecognition.stopListening();
    }
  }, [isConnected, micOn, listening, browserSupportsSpeechRecognition]);

  useEffect(() => {
    if (isConnected && !listening && micOn && transcript) {
      console.log(transcript);
      console.log("==== 区切り ====");
      axios.post('https://jsonplaceholder.typicode.com/posts', {
        title: 'Speech Transcript',
        body: `「${transcript}」`,
        userId: 1,
      }, {
        headers: {
          'Content-type': 'application/json; charset=UTF-8',
        },
      })
        .then((response) => console.log(response.data))
        .catch((error) => console.error('Error:', error));
      resetTranscript();
    }
  }, [isConnected, listening, micOn, transcript, resetTranscript]);

  return (
    <>
      <div className="room">
        {isConnected ? (
          <div className="user-list">
            <div className="user">
              <LocalUser
                audioTrack={localMicrophoneTrack}
                cameraOn={cameraOn}
                micOn={micOn}
                videoTrack={localCameraTrack}
                cover="https://www.agora.io/en/wp-content/uploads/2022/10/3d-spatial-audio-icon.svg"
              >
                <samp className="user-name">You</samp>
              </LocalUser>
            </div>
            {remoteUsers.map((user) => (
              <div className="user" key={user.uid}>
                <RemoteUser
                  cover="https://www.agora.io/en/wp-content/uploads/2022/10/3d-spatial-audio-icon.svg"
                  user={user}
                >
                  <samp className="user-name">{user.uid}</samp>
                </RemoteUser>
              </div>
            ))}
          </div>
        ) : (
          <div className="join-room">
            {/* <img alt="agora-logo" className="logo" src={logo} /> */}
            <input
              onChange={(e) => setAppId(e.target.value)}
              placeholder="<Your app ID>"
              value={appId}
            />
            <input
              onChange={(e) => setChannel(e.target.value)}
              placeholder="<Your channel Name>"
              value={channel}
            />
            <input
              onChange={(e) => setToken(e.target.value)}
              placeholder="<Your token>"
              value={token}
            />

            <button
              className={`join-channel ${!appId || !channel ? "disabled" : ""}`}
              disabled={!appId || !channel}
              onClick={() => setCalling(true)}
            >
              <span>Join Channel</span>
            </button>
          </div>
        )}
      </div>
      {isConnected && (
        <div className="control">
          <div className="left-control">
            <button className="btn" onClick={() => setMic((a) => !a)}>
              <i className={`i-microphone ${!micOn ? "off" : ""}`} />
            </button>
            <button className="btn" onClick={() => setCamera((a) => !a)}>
              <i className={`i-camera ${!cameraOn ? "off" : ""}`} />
            </button>
          </div>
          <button
            className={`btn btn-phone ${calling ? "btn-phone-active" : ""}`}
            onClick={() => setCalling((a) => !a)}
          >
            {calling ? (
              <i className="i-phone-hangup" />
            ) : (
              <i className="i-mdi-phone" />
            )}
          </button>
        </div>
      )}
    </>
  );
};

export default MeetingProgress;
