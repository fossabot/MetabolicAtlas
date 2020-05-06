import axios from 'axios';

const fetchSubsystemSummary = async ({ id, version }) => {
  const { data } = await axios({ url: `${version}/subsystems/${id}/`, baseURL: '/new_api/integrated' });
  return data;
};
export default { fetchSubsystemSummary };
