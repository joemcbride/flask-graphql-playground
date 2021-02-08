import { useState } from 'react'
import { hot } from 'react-hot-loader/root'
import './app.css'

const App = () => {
  const [value, setValue] = useState(0)
  console.log('value', value)
  return (
    <div>
      <h1>Webpack Dev Server</h1>
      <button onClick={() => setValue(value + 1)}>Like</button>
      <div>Count: {value}</div>
    </div>
  )
}

export default hot(App)
