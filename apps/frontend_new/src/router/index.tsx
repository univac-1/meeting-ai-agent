import { Suspense, lazy } from "react"
import { Route, createHashRouter, RouterProvider, createRoutesFromElements } from "react-router-dom"

const HomePage = lazy(() => import("../pages/home"))
const MeetingSchedulePage = lazy(() => import("../pages/meetingSchedule"))
const MeetingInfoPage = lazy(() => import("../pages/meetingInfo"))
const JoinPage = lazy(() => import("../pages/join"))
const MeetingPage = lazy(() => import("../pages/meeting"))
const NotFoundPage = lazy(() => import("../pages/404"))

const routerItems = [
  <Route path="/" element={<HomePage />} />,
  <Route path="/home" element={<HomePage />} />,
  <Route path="/meeting/schedule" element={<MeetingSchedulePage />} />,
  <Route path="/meeting/:meetingId" element={<MeetingInfoPage />} />,
  <Route path="/join" element={<JoinPage />} />,
  <Route path="/meeting" element={<MeetingPage />} />,
  <Route path="*" element={<NotFoundPage />} />,
]

const router = createHashRouter(createRoutesFromElements(routerItems))

export const RouteContainer = () => {
  return <RouterProvider router={router} future={{ v7_startTransition: true }}></RouterProvider>
}
