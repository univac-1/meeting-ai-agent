import { useEffect, useState } from "react";
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
import {
  DatePicker,
  TimePicker,
  LocalizationProvider,
} from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import DeleteIcon from "@mui/icons-material/Delete";
import MeetingURLConfirmation from "./MeetingURLConfirmation";
import { CLOUD_RUN_ENDPOINT } from "./config";
import dayjs from "dayjs";

const MeetingSetup = () => {
  const [meetingName, setMeetingName] = useState("");
  const [meetingPurpose, setMeetingPurpose] = useState("");
  const [startDate, setStartDate] = useState(dayjs());
  const [startTime, setStartTime] = useState(dayjs());
  const [endTime, setEndTime] = useState(dayjs());
  const [participants, setParticipants] = useState<string[]>([""]);
  const [agenda, setAgenda] = useState<{ topic: string; duration: string }[]>([
    { topic: "", duration: "" },
  ]);
  const [isMeetingCreated, setIsMeetingCreated] = useState(false);
  const [meetingId, setMeetingId] = useState("");

  useEffect(() => {
    // startTime が変更されたら endTime を 1 時間後に設定
    setEndTime(startTime.add(1, "hour"));
  }, [startTime]);

  const handleSave = async () => {
    try {
      const response = await fetch(`${CLOUD_RUN_ENDPOINT}/meeting`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          meeting_name: meetingName,
          meeting_purpose: meetingPurpose,
          start_date: startDate.format("YYYY-MM-DD"),
          start_time: startTime.format("HH:mm"),
          end_time: endTime.format("HH:mm"),
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

  const handleRemoveAgenda = (index: number) => {
    const updatedAgenda = agenda.filter((_, i) => i !== index);
    setAgenda(updatedAgenda);
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
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
                  multiline
                  rows={4}
                  placeholder="例: チームメンバー間で進捗を確認し、次のタスクの優先順位を決定する"
                  label="会議の目的"
                  value={meetingPurpose}
                  onChange={(e) => setMeetingPurpose(e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <DatePicker
                  label="開始日"
                  value={startDate}
                  onChange={(newValue) => setStartDate(newValue)}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </Grid>
              <Grid item xs={6}>
                <TimePicker
                  label="開始時刻"
                  value={startTime}
                  onChange={(newValue) => setStartTime(newValue)}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </Grid>
              <Grid item xs={6}>
                <TimePicker
                  label="終了時刻"
                  value={endTime}
                  onChange={(newValue) => setEndTime(newValue)}
                  renderInput={(params) => <TextField {...params} fullWidth />}
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
                              setParticipants(
                                participants.filter((_, i) => i !== index)
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
                  <Grid container spacing={2} key={index}>
                    <Grid item xs={8}>
                      <TextField
                        fullWidth
                        label={`アジェンダ ${index + 1}`}
                        value={item.topic}
                        onChange={(e) => {
                          const newAgenda = [...agenda];
                          newAgenda[index].topic = e.target.value;
                          setAgenda(newAgenda);
                        }}
                      />
                    </Grid>
                    <Grid item xs={3}>
                      <TextField
                        fullWidth
                        type="number"
                        label="所要時間 (分)"
                        value={item.duration}
                        onChange={(e) => {
                          const newAgenda = [...agenda];
                          newAgenda[index].duration = e.target.value;
                          setAgenda(newAgenda);
                        }}
                      />
                    </Grid>
                    <Grid item xs={1}>
                      <IconButton
                        color="secondary"
                        onClick={() => handleRemoveAgenda(index)}
                        disabled={agenda.length === 1}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Grid>
                  </Grid>
                ))}
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() =>
                    setAgenda([...agenda, { topic: "", duration: "" }])
                  }
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
    </LocalizationProvider>
  );
};

export default MeetingSetup;
