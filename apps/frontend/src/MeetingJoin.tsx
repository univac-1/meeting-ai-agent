import React, { useState } from "react";
import { Button, TextField } from "@mui/material";
import { useNavigate } from "react-router-dom";

const MeetingJoin = () => {
  const [username, setUsername] = useState("");
  const navigate = useNavigate();

  const handleJoin = () => {
    console.log(`ユーザ名: ${username} が会議に参加しました`);
    navigate("/confirmation"); // 会議URL確認画面に遷移
  };

  return (
    <div>
      <h1>会議参加画面</h1>
      <TextField
        label="ユーザ名"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <Button variant="contained" onClick={handleJoin}>
        会議参加
      </Button>
    </div>
  );
};

export default MeetingJoin;
