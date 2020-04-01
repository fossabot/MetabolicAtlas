import axios from 'axios';

const fetchSubsystemSummary = async (model, subsystemId) => {
  const { data } = await axios.get(`${model}/subsystem/${subsystemId}/summary/`);
  return data;
};

export default { fetchSubsystemSummary };
