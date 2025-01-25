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

interface MeetingURLConfirmationProps {
  meetingId: string;
}

const MeetingURLConfirmation: React.FC<MeetingURLConfirmationProps> = ({
  meetingId,
}) => {
  const meetingURL = `https://ai-agent-hackthon-with-goole.web.app/meeting/${meetingId}`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(meetingURL);
    alert("URLがクリップボードにコピーされました");
  };

  return (
    <StyledContainer maxWidth="md">
      <StyledPaper elevation={3}>
        <Typography variant="h4" gutterBottom>
          会議URLの確認画面
        </Typography>
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
