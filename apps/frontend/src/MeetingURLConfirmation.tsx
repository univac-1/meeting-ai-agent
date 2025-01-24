import { Button, Container, Typography, Paper } from "@mui/material";
import { styled } from "@mui/system";

const StyledContainer = styled(Container)({
  marginTop: "20px",
  padding: "20px",
});

const StyledPaper = styled(Paper)({
  padding: "20px",
  textAlign: "center",
});

const MeetingURLConfirmation = () => {
  const meetingURL = "http://example.com/meeting"; // 仮のURL

  const copyToClipboard = () => {
    navigator.clipboard.writeText(meetingURL);
    alert("URLがクリップボードにコピーされました");
  };

  return (
    <StyledContainer maxWidth="sm">
      <StyledPaper elevation={3}>
        <Typography variant="h4" gutterBottom>
          会議URLの確認画面
        </Typography>
        <Typography variant="body1">会議名: 会議のタイトル</Typography>
        <Typography variant="body1">会議の日時: 2025-01-24 10:00</Typography>
        <Typography variant="body1">
          会議URL: {meetingURL}
          <Button
            variant="contained"
            onClick={copyToClipboard}
            style={{
              marginLeft: "10px",
              padding: "5px 10px",
              minWidth: "auto",
            }}
          >
            コピー
          </Button>
        </Typography>
      </StyledPaper>
    </StyledContainer>
  );
};

export default MeetingURLConfirmation;
