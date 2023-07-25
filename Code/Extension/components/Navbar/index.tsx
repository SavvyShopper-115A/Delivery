import { Button, Navbar } from "@nextui-org/react"
import React from "react"

import { useFirebase } from "~firebase/hook"

const NavbarComponent = () => {
  const { user, isLoading, onLogin, onLogout } = useFirebase()
  return (
    <Navbar isBordered variant="static" className="z-50">
      <a
        href="http://savvy-shopper-frontend.vercel.app/"
        target="_blank"
        rel="noopener noreferrer"
        style={{
          textDecoration: "none",
          color: "inherit",
          display: "flex",
          alignItems: "center"
        }}>
        <Navbar.Brand>
          <div style={{display: 'flex', flexDirection: 'row', alignItems: 'center'}}>
            <img
              src="https://i.imgur.com/FLpXCki.png"
              alt="Company Logo"
              width={30}
              height={36}
              style={{
                marginRight: "0.75rem",
                textDecoration: "none",
                color: "inherit"
              }}
            />

            <div style={{ textDecoration: "none", color: "inherit" }}>
              SaavyShopper
            </div>
          </div>
        </Navbar.Brand>
      </a>
      <Navbar.Content>
        {!user ? (
          <Button size="xs" light color="primary" onClick={() => onLogin()}>
            Log in
          </Button>
        ) : (
          <Button size="xs" light color="error" onClick={() => onLogout()}>
            Log out
          </Button>
        )}
      </Navbar.Content>
    </Navbar>
  )
}

export default NavbarComponent
