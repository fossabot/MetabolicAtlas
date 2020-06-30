import axios from 'axios';

const fetchSubsystemSummary = async ({ id, version }) => {
  const { data } = await axios.get(`${version}/subsystems/${id}/`);
  return data;
};

export default { fetchSubsystemSummary };
