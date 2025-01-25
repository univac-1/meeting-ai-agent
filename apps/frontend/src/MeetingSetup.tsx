import { useState } from "react";
import {
  Button,
  TextField,
  Container,
  Grid,
  Typography,
  Paper,
  IconButton,
  InputAdornment,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import MeetingURLConfirmation from "./MeetingURLConfirmation";
import { CLOUD_RUN_ENDPOINT } from "./config";

const MeetingSetup = () => {
  const [meetingName, setMeetingName] = useState("");
  const [participants, setParticipants] = useState<string[]>([""]);
  const [agenda, setAgenda] = useState<string[]>([""]);
  const [isMeetingCreated, setIsMeetingCreated] = useState(false);
  const [meetingId, setMeetingId] = useState("");

  const handleSave = async () => {
    try {
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
    } catch (error) {
      console.error("Error while saving meeting:", error);
    }
  };

  const handleRemoveItem = (
    index: number,
    setState: React.Dispatch<React.SetStateAction<string[]>>,
    state: string[]
  ) => {
    const updatedState = state.filter((_, i) => i !== index);
    setState(updatedState);
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
              <Typography variant="h6" gutterBottom>
                参加者リスト
              </Typography>
              {participants.map((participant, index) => (
                <TextField
                  key={index}
                  fullWidth
                  label={`参加者 ${index + 1}`}
                  value={participant}
                  onChange={(e) => {
                    const newParticipants = [...participants];
                    newParticipants[index] = e.target.value;
                    setParticipants(newParticipants);
                  }}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          color="secondary"
                          onClick={() =>
                            handleRemoveItem(
                              index,
                              setParticipants,
                              participants
                            )
                          }
                          disabled={participants.length === 1}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              ))}
              <Button
                variant="contained"
                color="primary"
                onClick={() => setParticipants([...participants, ""])}
                style={{ marginTop: "10px" }}
              >
                参加者を追加
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                アジェンダ
              </Typography>
              {agenda.map((item, index) => (
                <TextField
                  key={index}
                  fullWidth
                  label={`アジェンダ ${index + 1}`}
                  value={item}
                  onChange={(e) => {
                    const newAgenda = [...agenda];
                    newAgenda[index] = e.target.value;
                    setAgenda(newAgenda);
                  }}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          color="secondary"
                          onClick={() =>
                            handleRemoveItem(index, setAgenda, agenda)
                          }
                          disabled={agenda.length === 1}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              ))}
              <Button
                variant="contained"
                color="primary"
                onClick={() => setAgenda([...agenda, ""])}
                style={{ marginTop: "10px" }}
              >
                アジェンダを追加
              </Button>
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
