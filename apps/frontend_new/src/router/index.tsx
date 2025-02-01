import { Suspense, lazy } from "react"
import { Route, createHashRouter, RouterProvider, createRoutesFromElements } from "react-router-dom"

const HomePage = lazy(() => import("../pages/home"))
const SchedulePage = lazy(() => import("../pages/schedule"))
const JoinPage = lazy(() => import("../pages/join"))
const MeetingPage = lazy(() => import("../pages/meeting"))
const NotFoundPage = lazy(() => import("../pages/404"))

const routerItems = [
  <Route path="/" element={<HomePage />} />,
  <Route path="/home" element={<HomePage />} />,
  <Route path="/schedule" element={<SchedulePage />} />,
  <Route path="/join" element={<JoinPage />} />,
  <Route path="/meeting" element={<MeetingPage />} />,
  <Route path="*" element={<NotFoundPage />} />,
]

const router = createHashRouter(createRoutesFromElements(routerItems))

export const RouteContainer = () => {
  return <RouterProvider router={router} future={{ v7_startTransition: true }}></RouterProvider>
}
