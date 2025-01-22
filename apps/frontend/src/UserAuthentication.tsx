import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // 追加

const UserAuthentication = () => {
  const [appID, setAppID] = useState("");
  const [channelName, setChannelName] = useState("");
  const [token, setToken] = useState("");
  const navigate = useNavigate(); // 追加

  const handleJoin = () => {
    if (appID && channelName) {
      // MeetingProgressに遷移し、値を渡す
      navigate("/meeting-progress", { state: { appID, channelName, token } });
    } else {
      alert("Please enter Agora App ID and Channel Name");
    }
  };

  return (
    <div>
      <p>Please enter your Agora AppID and Channel Name</p>
      <label htmlFor="appid">Agora App ID: </label>
      <input
        id="appid"
        type="text"
        value={appID}
        onChange={(e) => setAppID(e.target.value)}
        placeholder="required"
      />
      <br />
      <br />
      <label htmlFor="channel">Channel Name: </label>
      <input
        id="channel"
        type="text"
        value={channelName}
        onChange={(e) => setChannelName(e.target.value)}
        placeholder="required"
      />
      <br />
      <br />
      <label htmlFor="token">Channel Token: </label>
      <input
        id="token"
        type="text"
        value={token}
        onChange={(e) => setToken(e.target.value)}
        placeholder="optional"
      />
      <br />
      <br />
      <button onClick={handleJoin}>Join</button>
    </div>
  );
};

export default UserAuthentication;
