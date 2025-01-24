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

const MeetingSetup = () => {
  const [meetingName, setMeetingName] = useState("");
  const [meetingDate, setMeetingDate] = useState("");
  const [participants, setParticipants] = useState("");
  const [agenda, setAgenda] = useState("");
  const [isMeetingCreated, setIsMeetingCreated] = useState(false);
  const handleSave = async () => {
    const response = await fetch(
      "https://meeting-ai-agent-132459894103.asia-northeast1.run.app/",
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (response.ok) {
      const data = await response;
      console.log("Meeting ID:", data);
      setIsMeetingCreated(true);
    } else {
      console.error("Failed to create meeting");
    }
  };
  return (
    <Container maxWidth="sm">
      {isMeetingCreated ? (
        <MeetingURLConfirmation />
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
                label="会議の日時"
                type="datetime-local"
                value={meetingDate}
                onChange={(e) => setMeetingDate(e.target.value)}
                InputLabelProps={{
                  shrink: true,
                }}
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
