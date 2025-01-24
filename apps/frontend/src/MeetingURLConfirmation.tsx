import React from "react";
import { Button } from "@mui/material";

const MeetingURLConfirmation = () => {
  const meetingURL = "http://example.com/meeting"; // 仮のURL

  const copyToClipboard = () => {
    navigator.clipboard.writeText(meetingURL);
    alert("URLがクリップボードにコピーされました");
  };

  return (
    <div>
      <h1>会議URLの確認画面</h1>
      <p>会議名: 会議のタイトル</p>
      <p>会議URL: {meetingURL}</p>
      <p>会議の日時: 2025-01-24 10:00</p>
      <Button variant="contained" onClick={copyToClipboard}>
        コピー
      </Button>
    </div>
  );
};

export default MeetingURLConfirmation;
