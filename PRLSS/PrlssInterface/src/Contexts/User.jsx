import { createContext, useContext, useState } from "react";

// Context stores exactly 3 fields: name, budget, city
const UserContext = createContext(null);

export function UserProvider({ children }) {
  const [user, setUser] = useState({
    name: "",
    budget: "",
    city: "",
  });

  const updateUser = (fields) => {
    setUser((prev) => ({ ...prev, ...fields }));
  };

  return (
    <UserContext.Provider value={{ user, updateUser }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}

export default UserContext;
