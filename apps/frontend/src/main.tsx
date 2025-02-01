import React, { Suspense } from "react"
import ReactDOM from "react-dom/client"
import App from "./App.tsx"
import store from "./store"
import { Provider } from "react-redux"
import { ConfigProvider } from "antd"

import "./styles/reset.css"
import "./styles/global.css"

const theme = {
  token: {
    colorPrimary: "#3d53f5",
    colorInfo: "#3d53f5",
  },
  components: {
    Switch: {
      trackHeight: 24,
      handleSize: 20,
    },
  },
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <Provider store={store}>
    <ConfigProvider theme={theme}>
      <Suspense fallback={"loading..."}>
        <App />
      </Suspense>
    </ConfigProvider>
  </Provider>,
)
