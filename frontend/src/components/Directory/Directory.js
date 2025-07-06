import React, { useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import { toast } from 'react-toastify';
import {
  FaPlus,
  FaArrowUp,
  FaArrowDown,
  FaTrash,
  FaEdit,
  FaKey,
  FaSearch,
} from "react-icons/fa";
import "../../assets/styles/Directory.css";
import 'react-toastify/dist/ReactToastify.css';
import {
  fetchUsers,createUser, promoteUser,demoteUser,deleteUser,changePassword,
} from "../../services/userService";
import { contactService } from "../../services/contactServices";

function Directory() {
  const [contacts, setContacts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [passwordData, setPasswordData] = useState({
    oldPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [newUser, setNewUser] = useState({
    username: "",
    first_name: "",
    last_name: "",
    password: "",
    adresse: "",
    num_phone: "",
  });

  const [isAdmin, setIsAdmin] = useState(false);
  const [currentUserId, setCurrentUserId] = useState(null);

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editUser, setEditUser] = useState({
    id: null,
    username: "",
    first_name: "",
    last_name: "",
    adresse: "",
    num_phone: "",
  });

  // Charger les utilisateurs et décoder le token JWT
  const loadData = async () => {
    try {
      const token = localStorage.getItem("token");
      if (token) {
        const decoded = jwtDecode(token);
        setIsAdmin(decoded.role === "admin");
        setCurrentUserId(decoded.user_id);
      }

      const data = await fetchUsers(searchTerm);
      setContacts(data);
      setIsLoading(false);
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };
  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      loadData();
    }, 300);

    return () => clearTimeout(debounceTimer);
  }, [searchTerm]);

  // Dans le composant Directory
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Log pour déboguer
      console.log("Données envoyées:", newUser);

      // S'assurer que tous les champs sont remplis
      if (
        !newUser.username ||
        !newUser.first_name ||
        !newUser.last_name ||
        !newUser.password ||
        !newUser.adresse ||
        !newUser.num_phone
      ) {
        throw new Error("Tous les champs sont requis");
      }

      // Créer l'objet exactement comme attendu par l'API
      const userData = {
        username: newUser.username,
        first_name: newUser.first_name,
        last_name: newUser.last_name,
        password: newUser.password,
        adresse: newUser.adresse,
        num_phone: newUser.num_phone,
      };

      // Appeler le service de création d'utilisateur
      const response = await createUser(userData);
      console.log("Réponse:", response);

      setIsModalOpen(false);
      setNewUser({
        username: "",
        first_name: "",
        last_name: "",
        password: "",
        adresse: "",
        num_phone: "",
      });
      loadData();
    } catch (err) {
      // Log détaillé de l'erreur
      console.error("Erreur détaillée:", err);
      setError(err.message);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError("Les mots de passe ne correspondent pas");
      return;
    }
    let response
    try {
      // Check if the admin is changing their own password or another user's password
      if (selectedUserId === currentUserId) {
        response = await changePassword(
          currentUserId,
          passwordData.oldPassword,
          passwordData.newPassword
        );
      } else if (isAdmin) {
        // Admin can change password for other users
        response = await changePassword(selectedUserId, passwordData.oldPassword, passwordData.newPassword); // Provide the new password directly for other users
      } else {
        setError("Vous ne pouvez modifier que votre propre mot de passe.");
        return;
      }
      toast(response.message)
      setIsPasswordModalOpen(false);
      setPasswordData({
        oldPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const openPasswordModal = (userId) => {
    setSelectedUserId(userId);
    setIsPasswordModalOpen(true);
    setError(null);
  };
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewUser((prev) => ({
      ...prev,
      [name]: value,
    }));
  };
  const handlePromote = async (userId) => {
    try {
      await promoteUser(userId);
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDemote = async (userId) => {
    try {
      await demoteUser(userId);
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (userId) => {
    if (
      window.confirm("Êtes-vous sûr de vouloir supprimer cet utilisateur ?")
    ) {
      try {
        await deleteUser(userId);
        loadData();
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const handleEditClick = (user) => {
    setEditUser({
      id: user.id,
      username: user.username,
      first_name: user.first_name,
      last_name: user.last_name,
      adresse: user.adresse,
      num_phone: user.num_phone,
    });
    setIsEditModalOpen(true);
  };

  const handleEditInputChange = (e) => {
    const { name, value } = e.target;
    setEditUser((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      await contactService.updateContact(editUser.id, editUser);
      setIsEditModalOpen(false);
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  if (isLoading) return <div>Chargement...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!contacts?.length) {
    return (
      <div className="no-results">
        <p>Aucun utilisateur trouvé.</p>
        {searchTerm && (
          <button className="clear-search" onClick={() => setSearchTerm("")}>
            Effacer la recherche
          </button>
        )}
      </div>
    );
  }
  return (
    <div className="directory-container">
      {isAdmin ? (
        <div className="top-controls">
          <button onClick={() => setIsModalOpen(true)} className="add-button">
            <FaPlus /> Ajouter un utilisateur
          </button>

          <div className="search-container">
            <FaSearch className="search-icon" />
            <input
              type="text"
              placeholder="Rechercher des utilisateurs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
        </div>
      ) : (
        <div className="search-container">
          <FaSearch className="search-icon" />
          <input
            type="text"
            placeholder="Rechercher des utilisateurs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      )}

      {/* Modal existante pour l'ajout d'utilisateur */}
      {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <h2>Ajouter un nouvel utilisateur</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <input
                  type="text"
                  name="username"
                  placeholder="Nom d'utilisateur"
                  value={newUser.username}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <input
                  type="text"
                  name="first_name"
                  placeholder="Prénom"
                  value={newUser.first_name}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <input
                  type="text"
                  name="last_name"
                  placeholder="Nom"
                  value={newUser.last_name}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <input
                  type="password"
                  name="password"
                  placeholder="Mot de passe"
                  value={newUser.password}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <input
                  type="text"
                  name="adresse"
                  placeholder="Adresse"
                  value={newUser.adresse}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <input
                  type="tel"
                  name="num_phone"
                  placeholder="Numéro de téléphone"
                  value={newUser.num_phone}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                />
              </div>

              <div className="button-group">
                <button type="submit" className="submit-button">
                  Ajouter
                </button>
                <button
                  type="button"
                  className="cancel-button"
                  onClick={() => {
                    setIsModalOpen(false);
                    setNewUser({
                      username: "",
                      first_name: "",
                      last_name: "",
                      password: "",
                      adresse: "",
                      num_phone: "",
                    });
                  }}
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

{isPasswordModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <h2>Changer le mot de passe</h2>
            <form onSubmit={handlePasswordSubmit}>
              {selectedUserId === currentUserId && (
                <input
                  type="password"
                  placeholder="Ancien mot de passe"
                  value={passwordData.oldPassword}
                  onChange={(e) =>
                    setPasswordData((prev) => ({
                      ...prev,
                      oldPassword: e.target.value,
                    }))
                  }
                  required
                />
              )}
              <input
                type="password"
                placeholder="Nouveau mot de passe"
                value={passwordData.newPassword}
                onChange={(e) =>
                  setPasswordData((prev) => ({
                    ...prev,
                    newPassword: e.target.value,
                  }))
                }
                required
              />
              <input
                type="password"
                placeholder="Confirmer le nouveau mot de passe"
                value={passwordData.confirmPassword}
                onChange={(e) =>
                  setPasswordData((prev) => ({
                    ...prev,
                    confirmPassword: e.target.value,
                  }))
                }
                required
              />
              <div className="button-group">
                <button type="submit">Changer</button>
                <button
                  type="button"
                  onClick={() => setIsPasswordModalOpen(false)}
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Add Edit Modal */}
      {isEditModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <h2>Modifier l'utilisateur {editUser.username}</h2>
            <form onSubmit={handleEditSubmit}>
              <div className="form-group">
                <input
                  type="text"
                  name="first_name"
                  placeholder="Prénom"
                  value={editUser.first_name}
                  onChange={handleEditInputChange}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <input
                  type="text"
                  name="last_name"
                  placeholder="Nom"
                  value={editUser.last_name}
                  onChange={handleEditInputChange}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <input
                  type="text"
                  name="adresse"
                  placeholder="Adresse"
                  value={editUser.adresse}
                  onChange={handleEditInputChange}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <input
                  type="tel"
                  name="num_phone"
                  placeholder="Numéro de téléphone"
                  value={editUser.num_phone}
                  onChange={handleEditInputChange}
                  required
                  className="form-input"
                />
              </div>

              <div className="button-group">
                <button type="submit" className="submit-button">
                  Enregistrer
                </button>
                <button
                  type="button"
                  className="cancel-button"
                  onClick={() => setIsEditModalOpen(false)}
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      <ul className="users-list">
        {contacts.map((user) => (
          <li key={user.id} className="user-item">
            <div className="user-info">
              
              <div className="user-primary-info">
                {user.id === currentUserId && (
                  <span className="current-user-indicator"></span>
                )}
                <strong>
                  {user.first_name} {user.last_name}
                </strong>{" "}
                - {user.username}
                {user.role && <span className="role-badge">{user.role}</span>} - 
                  <span className="phone-info">
                    📞  : {user.num_phone}
                  </span>
                  <span className="address-info">
                    📍 : {user.adresse}
                  </span>
              </div>
            </div>
            <div className="user-actions">
              {(isAdmin || user.id === currentUserId) && (
                  <button
                    onClick={() => handleEditClick(user)}
                    className="action-button edit"
                    title="Modifier"
                  >
                    <FaEdit />
                  </button>
                )}
              {isAdmin && user.role !== "admin" && (
                <button
                  onClick={() => handlePromote(user.id)}
                  className="action-button promote"
                  title="Promouvoir en admin"
                >
                  <FaArrowUp />
                </button>
              )}
              {isAdmin &&
                user.role === "admin" &&
                user.id !== currentUserId && (
                  <button
                    onClick={() => handleDemote(user.id)}
                    className="action-button demote"
                    title="Rétrograder"
                  >
                    <FaArrowDown />
                  </button>
                )}
              {(isAdmin || user.id === currentUserId) && (
                <button
                  onClick={() => openPasswordModal(user.id)}
                  className="action-button password"
                  title="Changer le mot de passe"
                >
                  <FaKey />
                </button>
              )}
              {(isAdmin || user.id === currentUserId) && (
                <button
                  onClick={() => handleDelete(user.id)}
                  className="action-button delete"
                  title="Supprimer"
                >
                  <FaTrash />
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Directory;