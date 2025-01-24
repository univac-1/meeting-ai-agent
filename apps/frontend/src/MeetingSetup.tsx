import React, { useState } from "react";
import { Button, TextField } from "@mui/material";

const MeetingSetup = () => {
  const [meetingName, setMeetingName] = useState("");
  const [meetingDate, setMeetingDate] = useState("");
  const [participants, setParticipants] = useState("");
  const [agenda, setAgenda] = useState("");

  const handleSave = () => {
    console.log({ meetingName, meetingDate, participants, agenda });
  };

  return (
    <div>
      <h1>会議の初期設定画面</h1>
      <TextField
        label="会議名"
        value={meetingName}
        onChange={(e) => setMeetingName(e.target.value)}
      />
      <TextField
        label="会議の日時"
        type="datetime-local"
        value={meetingDate}
        onChange={(e) => setMeetingDate(e.target.value)}
      />
      <TextField
        label="参加者リスト（ユーザ名）"
        value={participants}
        onChange={(e) => setParticipants(e.target.value)}
      />
      <TextField
        label="アジェンダ"
        value={agenda}
        onChange={(e) => setAgenda(e.target.value)}
      />
      <Button variant="contained" onClick={handleSave}>
        保存
      </Button>
      <Button variant="outlined" onClick={() => console.log("キャンセル")}>
        キャンセル
      </Button>
    </div>
  );
};

export default MeetingSetup;
