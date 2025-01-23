import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./Home"; // 追加
import MeetingSetup from "./MeetingSetup";
import MeetingURLConfirmation from "./MeetingURLConfirmation";
import UserAuthentication from "./UserAuthentication";
import MeetingProgress from "./MeetingProgress";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/setup" element={<MeetingSetup />} />
        <Route
          path="/confirmation"
          element={
            <MeetingURLConfirmation
              meeting={{ name: "hoge", url: "fuga", date: "piyo" }}
            />
          }
        />
        <Route path="/auth" element={<UserAuthentication />} />
        <Route path="/meeting-progress" element={<MeetingProgress />} />
      </Routes>
    </Router>
  );
};

export default App;
