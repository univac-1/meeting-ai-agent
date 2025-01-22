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
import { useState } from "react";
import { useLocation } from "react-router-dom"; // 追加

import "./index.css";

const MeetingProgress = () => {
  const location = useLocation(); // 追加
  const { appID, channelName, token } = location.state || {}; // 追加

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
          <div className="join-form">
            <h2>Join Video Call</h2>
            <input
              type="text"
              placeholder="App ID"
              value={appId}
              onChange={(e) => setAppId(e.target.value)}
            />
            <input
              type="text"
              placeholder="Channel Name"
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
            />
            <input
              type="text"
              placeholder="Token (optional)"
              value={tokenValue}
              onChange={(e) => setToken(e.target.value)}
            />
            <button
              onClick={() => setCalling(true)}
              disabled={!appId || !channel}
            >
              Join Channel
            </button>
          </div>
        )}
      </div>
      {isConnected && (
        <div className="controls">
          <button onClick={() => setMic((a) => !a)}>
            {micOn ? "Turn Off Mic" : "Turn On Mic"}
          </button>
          <button onClick={() => setCamera((a) => !a)}>
            {cameraOn ? "Turn Off Camera" : "Turn On Camera"}
          </button>
          <button onClick={() => setCalling((a) => !a)}>
            {calling ? "End Call" : "Start Call"}
          </button>
        </div>
      )}
    </>
  );
};

export default MeetingProgress;
