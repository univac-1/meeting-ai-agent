import { useState } from "react";
import {
  Button,
  TextField,
  Container,
  Grid,
  Typography,
  Paper,
} from "@mui/material";
import MeetingURLConfirmation from "./MeetingURLConfirmation";
import { CLOUD_RUN_ENDPOINT } from "./config";
const MeetingSetup = () => {
  const [meetingName, setMeetingName] = useState("");
  const [participants, setParticipants] = useState("");
  const [agenda, setAgenda] = useState("");
  const [isMeetingCreated, setIsMeetingCreated] = useState(false);
  const [meetingId, setMeetingId] = useState("");

  const handleSave = async () => {
    const response = await fetch(`${CLOUD_RUN_ENDPOINT}/meeting`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        meeting_name: meetingName,
        participants,
        agenda,
      }),
    });
    if (response.ok) {
      const data = await response.json();
      console.log("Meeting ID:", data.data.meeting_id);
      setMeetingId(data.data.meeting_id);
      setIsMeetingCreated(true);
    } else {
      console.error("Failed to create meeting");
    }
  };

  return (
    <Container maxWidth="sm">
      {isMeetingCreated ? (
        <MeetingURLConfirmation meetingId={meetingId} />
      ) : (
        <Paper elevation={3} style={{ padding: "20px", marginTop: "20px" }}>
          <Typography variant="h4" gutterBottom>
            会議の初期設定画面
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="会議名"
                value={meetingName}
                onChange={(e) => setMeetingName(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="参加者リスト（ユーザ名）"
                value={participants}
                onChange={(e) => setParticipants(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="アジェンダ"
                value={agenda}
                onChange={(e) => setAgenda(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleSave}
                fullWidth
              >
                保存
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="outlined"
                color="secondary"
                onClick={() => console.log("キャンセル")}
                fullWidth
              >
                キャンセル
              </Button>
            </Grid>
          </Grid>
        </Paper>
      )}
    </Container>
  );
};

export default MeetingSetup;
