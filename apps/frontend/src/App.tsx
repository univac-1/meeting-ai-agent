import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./Home";
import MeetingSetup from "./MeetingSetup";
import MeetingApp from "./MeetingApp";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/setup" element={<MeetingSetup />} />
        <Route path="/meeting/:meetingId" element={<MeetingApp />} />
      </Routes>
    </Router>
  );
};

export default App;
